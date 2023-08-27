import subprocess
import sys
from pathlib import Path


def build_sunvalley():
    buildscript = Path.cwd() / "build.ps1"
    subprocess.run(["powershell", str(buildscript), "sv"])


def build_forest():
    rewriter = Path.cwd() / "tools" / "rewriter.py"
    subprocess.run([sys.executable, str(rewriter), "-r"])

    buildscript = Path.cwd() / "build.ps1"
    for theme in ("light", "dark"):
        subprocess.run(["powershell", str(buildscript), "fst", theme])

    subprocess.run([sys.executable, str(rewriter), "-c"])


def build_all():
    steps = (build_sunvalley, build_forest)
    [step() for step in steps]
