import subprocess
import sys
from pathlib import Path


def build_sunvalley():
    buildscript = Path.cwd() / 'build.ps1'
    subprocess.run(['powershell', str(buildscript), 'sunvalley'])


def build_forest():
    rewriter = Path.cwd() / 'tools' / 'rewriter.py'
    subprocess.run([sys.executable, str(rewriter), '--rewrite'])

    buildscript = Path.cwd() / 'build.ps1'
    for theme in ('light', 'dark'):
        subprocess.run(['powershell', str(buildscript), 'forest', theme])

    subprocess.run([sys.executable, str(rewriter), '--restore'])


def build_all():
    steps = (build_sunvalley, build_forest)
    [step() for step in steps]
